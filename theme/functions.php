<?php
/**
 * BizBot theme functions.
 *
 * Child theme of GeneratePress. Registers the Tool + News post types and the
 * tool_category taxonomy, and defines the ACF field group used on Tool
 * entries (category is handled by the taxonomy, not an ACF field).
 */

defined( 'ABSPATH' ) || exit;

/** Assets */
add_action( 'wp_enqueue_scripts', 'bizbot_enqueue_assets' );
function bizbot_enqueue_assets() {
	wp_enqueue_style( 'generatepress-style', get_template_directory_uri() . '/style.css' );
	wp_enqueue_style(
		'bizbot-style',
		get_stylesheet_uri(),
		array( 'generatepress-style' ),
		wp_get_theme()->get( 'Version' )
	);
}

/** Theme supports */
add_action( 'after_setup_theme', 'bizbot_theme_setup' );
function bizbot_theme_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script', 'navigation-widgets' ) );
	register_nav_menus(
		array(
			'primary' => __( 'Primary Menu', 'bizbot' ),
		)
	);
}

/**
 * "Tool" post type -> /tools/<slug>/, archive at /tools/.
 * Fields beyond title/content: outbound_url, logo_url, cta_label (via ACF below).
 * Category is the tool_category taxonomy so the homepage/directory filter
 * pills and the "Category: X; Y; Z" labels from the old site map cleanly.
 */
add_action( 'init', 'bizbot_register_tool_post_type' );
function bizbot_register_tool_post_type() {
	register_post_type(
		'tool',
		array(
			'label'        => __( 'Tools', 'bizbot' ),
			'public'       => true,
			'has_archive'  => 'tools',
			'rewrite'      => array( 'slug' => 'tools', 'with_front' => false ),
			'menu_icon'    => 'dashicons-hammer',
			'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
			'show_in_rest' => true,
		)
	);

	register_taxonomy(
		'tool_category',
		'tool',
		array(
			'label'        => __( 'Tool Categories', 'bizbot' ),
			'hierarchical' => true,
			'public'       => true,
			'rewrite'      => array( 'slug' => 'tool-category' ),
			'show_in_rest' => true,
		)
	);
}

/**
 * "News" post type -> /news/<slug>/, archive at /news/.
 */
add_action( 'init', 'bizbot_register_news_post_type' );
function bizbot_register_news_post_type() {
	register_post_type(
		'bb_news',
		array(
			'label'        => __( 'News', 'bizbot' ),
			'public'       => true,
			'has_archive'  => 'news',
			'rewrite'      => array( 'slug' => 'news', 'with_front' => false ),
			'menu_icon'    => 'dashicons-megaphone',
			'supports'     => array( 'title', 'editor', 'thumbnail', 'excerpt' ),
			'show_in_rest' => true,
		)
	);
}

/**
 * ACF field group for Tool entries. Registered in code (local field group)
 * so it's version-controlled and doesn't depend on manually rebuilding
 * fields in the ACF admin UI on a fresh install. Requires the free ACF
 * plugin to be active; no-ops harmlessly if it isn't.
 */
add_action( 'acf/init', 'bizbot_register_tool_fields' );
function bizbot_register_tool_fields() {
	if ( ! function_exists( 'acf_add_local_field_group' ) ) {
		return;
	}

	acf_add_local_field_group(
		array(
			'key'          => 'group_bizbot_tool',
			'title'        => 'Tool Details',
			'show_in_rest' => 1,
			'fields'       => array(
				array(
					'key'   => 'field_bizbot_outbound_url',
					'label' => 'Outbound / Affiliate URL',
					'name'  => 'outbound_url',
					'type'  => 'url',
					'instructions' => 'Where the "Get it" button sends visitors. Include any affiliate tracking params.',
				),
				array(
					'key'   => 'field_bizbot_logo_url',
					'label' => 'Logo URL',
					'name'  => 'logo_url',
					'type'  => 'url',
				),
				array(
					'key'          => 'field_bizbot_cta_label',
					'label'        => 'CTA Button Label',
					'name'         => 'cta_label',
					'type'         => 'text',
					'default_value' => 'Get it',
				),
			),
			'location' => array(
				array(
					array(
						'param'    => 'post_type',
						'operator' => '==',
						'value'    => 'tool',
					),
				),
			),
		)
	);
}

/**
 * Newsletter / tool-submission / guest-post-contact form shortcodes are
 * configured per-site (they depend on which form plugin is installed and
 * how each form is set up), so they're exposed as Customizer text fields
 * rather than hardcoded. Paste the plugin's shortcode (e.g. a MailPoet or
 * Fluent Forms shortcode) into Appearance -> Customize -> BizBot Forms.
 */
add_action( 'customize_register', 'bizbot_customize_register' );
function bizbot_customize_register( $wp_customize ) {
	$wp_customize->add_section(
		'bizbot_forms',
		array( 'title' => __( 'BizBot Forms', 'bizbot' ), 'priority' => 160 )
	);

	$form_settings = array(
		'bizbot_newsletter_shortcode'      => 'Newsletter signup shortcode',
		'bizbot_tool_submission_shortcode' => 'Tool submission shortcode',
		'bizbot_guest_post_contact_shortcode' => 'Guest post contact shortcode',
	);

	foreach ( $form_settings as $setting_id => $label ) {
		$wp_customize->add_setting( $setting_id, array( 'default' => '', 'sanitize_callback' => 'wp_kses_post' ) );
		$wp_customize->add_control(
			$setting_id,
			array(
				'label'   => $label,
				'section' => 'bizbot_forms',
				'type'    => 'text',
			)
		);
	}
}

/**
 * Render a configured form shortcode, or a friendly placeholder if the
 * admin hasn't set one up yet in the Customizer.
 */
function bizbot_render_form( string $customizer_key, string $placeholder_label ): void {
	$shortcode = get_theme_mod( $customizer_key, '' );
	if ( $shortcode ) {
		echo do_shortcode( $shortcode );
		return;
	}
	printf(
		'<p class="bb-form-placeholder">%s</p>',
		esc_html( sprintf( '%s form not configured yet — set it in Appearance → Customize → BizBot Forms.', $placeholder_label ) )
	);
}
